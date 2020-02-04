from lean_schema import post_process
import unittest
import os
import shutil

TEST_SRC_DIR = './test-src-dir'
TEST_DST_DIR = './test-dst-dir'
TEST_UNMATCHED_DIR = './test-unmatched-dir'

class TestPostProcess(unittest.TestCase):

    def tearDown(self):
        shutil.rmtree(TEST_SRC_DIR, ignore_errors=True)
        shutil.rmtree(TEST_DST_DIR, ignore_errors=True)
        shutil.rmtree(TEST_UNMATCHED_DIR, ignore_errors=True)

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

    def test_main_exits_if_src_dir_does_not_exist(self):
        os.mkdir(TEST_DST_DIR)

        with self.assertRaises(SystemExit) as se:
            post_process.main([
                "./test-src-dir-does-not-exist",
                TEST_DST_DIR
            ])
        assert se.exception.code == 1

        shutil.rmtree(TEST_DST_DIR)

    def test_main_exits_if_dst_dir_does_not_exist(self):
        os.mkdir(TEST_SRC_DIR)

        with self.assertRaises(SystemExit) as se:
            post_process.main([
                TEST_SRC_DIR,
                "./test-dst-dir-does-not-exist"
            ])
        assert se.exception.code == 1

        shutil.rmtree(TEST_SRC_DIR)

    def test_main_exits_with_invalid_copy_unmatched_files_flag(self):
        os.mkdir(TEST_SRC_DIR)
        os.mkdir(TEST_DST_DIR)

        with self.assertRaises(SystemExit) as se:
            post_process.main([
                "--copy-unmatched-files-dir", "./this-dir-does-not-exist",
                TEST_SRC_DIR,
                TEST_DST_DIR
                ])
        assert se.exception.code == 1

        shutil.rmtree(TEST_SRC_DIR)
        shutil.rmtree(TEST_DST_DIR)

    def test_main_copies_unmatched_files_with_flag(self):
        os.mkdir(TEST_SRC_DIR)
        os.mkdir(TEST_DST_DIR)
        os.mkdir(TEST_UNMATCHED_DIR)

        with open('{}/1.test'.format(TEST_SRC_DIR), 'w') as f:
            f.write("src")

        post_process.main([
            "--copy-unmatched-files-dir", TEST_UNMATCHED_DIR,
            "--src-files-extension", "test",
            TEST_SRC_DIR,
            TEST_DST_DIR
            ])

        assert os.path.isfile('{}/1.test'.format(TEST_UNMATCHED_DIR))
        assert os.path.isfile('{}/1.test'.format(TEST_DST_DIR)) == False

        shutil.rmtree(TEST_SRC_DIR)
        shutil.rmtree(TEST_DST_DIR)
        shutil.rmtree(TEST_UNMATCHED_DIR)

    def test_main_doesnt_copy_unmatched_files_without_flag(self):
        os.mkdir(TEST_SRC_DIR)
        os.mkdir(TEST_DST_DIR)

        with open('{}/1.test'.format(TEST_SRC_DIR), 'w') as f:
            f.write("src")

        post_process.main([
            "--src-files-extension", "test",
            TEST_SRC_DIR,
            TEST_DST_DIR
            ])

        assert os.path.isfile('{}/1.test'.format(TEST_DST_DIR)) == False

        shutil.rmtree(TEST_SRC_DIR)
        shutil.rmtree(TEST_DST_DIR)

    @unittest.mock.patch('builtins.print')
    def test_main_with_debug_outputs_more_information(self, builtins_print):
        os.mkdir(TEST_SRC_DIR)
        os.mkdir(TEST_DST_DIR)

        with open('{}/1.test'.format(TEST_SRC_DIR), 'w') as f:
            f.write("src")

        with open('{}/1.test'.format(TEST_DST_DIR), 'w') as f:
            f.write("dst")

        initial_call_count = builtins_print.call_count

        # without debug
        post_process.main([
            "--src-files-extension", "test",
            TEST_SRC_DIR,
            TEST_DST_DIR
            ])

        no_debug_call_count = builtins_print.call_count - initial_call_count

        # with debug
        post_process.main([
            "--src-files-extension", "test",
            "--debug",
            TEST_SRC_DIR,
            TEST_DST_DIR
            ])

        debug_call_count = builtins_print.call_count - no_debug_call_count

        assert debug_call_count > no_debug_call_count

        shutil.rmtree(TEST_SRC_DIR)
        shutil.rmtree(TEST_DST_DIR)

    # happy path
    def test_main_copies_files_correctly(self):
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
