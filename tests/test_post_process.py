from lean_schema import post_process
import unittest
import os
import shutil

class TestPostProcess(unittest.TestCase):

    def test_main_fails_without_src_dir(self):
        with self.assertRaises(SystemExit) as se:
            post_process.main([])
        assert se.exception.code == 2

    def test_main_fails_without_dst_dir(self):
        with self.assertRaises(SystemExit) as se:
            post_process.main(["./test-src-dir"])
        assert se.exception.code == 2

    def test_main_does_nothing_if_copy_is_false(self):
        with self.assertRaises(SystemExit) as se:
            post_process.main(["./test-src-dir", "./test-dst-dir", "--copy-codegen-files=false"])
        assert se.exception.code == 0

    def test_main_exits_if_dir_does_not_exist(self):
        with self.assertRaises(SystemExit) as se:
            post_process.main(["./test-src-dir-does-not-exist", "./test-dst-dir-does-not-exist"])
        assert se.exception.code == 1

    def test_main_copies_files_correctly(self):
        TEST_SRC_DIR = './test-src-dir'
        TEST_DST_DIR = './test-dst-dir'

        os.mkdir(TEST_SRC_DIR)
        os.mkdir(TEST_DST_DIR)

        with open('{}/1.test'.format(TEST_SRC_DIR), 'w') as f:
            f.write("src")

        with open('{}/1.test'.format(TEST_DST_DIR), 'w') as f:
            f.write("dst")

        post_process.main([
            "--src-files-extension", "test",
            TEST_SRC_DIR,
            TEST_DST_DIR
            ])

        with open('{}/1.test'.format(TEST_DST_DIR), 'r') as f:
            contents = f.read()
            assert "src" in contents
            assert "dst" not in contents

        shutil.rmtree(TEST_SRC_DIR)
        shutil.rmtree(TEST_DST_DIR)

if __name__ == '__main__':
    unittest.main()
