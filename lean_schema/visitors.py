from graphql.language.visitor import Visitor


class AllTypesVisitor(Visitor):
    """
    Visitor to get all referenced Types in a Query and collect them as
    a single Set. Abstract types are expanded in get_types.py, then the
    entire Root Set is passed to decomp.py to create the actual sub-graph.

    """

    __slots__ = ("context",)

    def __init__(self, context):
        self.types = set()
        self.context = context

    def enter(
        self,
        node,  # type: Field
        key,  # type: int
        parent,  # type: Union[List[Union[Field, InlineFragment]], List[Field]]
        path,  # type: List[Union[int, str]]
        ancestors,  # type: List[Any]
    ):
        self.types.add(self.context.get_type())
        self.types.add(self.context.get_input_type())
        self.types.add(self.context.get_parent_type())
        self.types.add(self.context.get_parent_input_type())

    def enter_FragmentSpread(
        self,
        node,  # type: Field
        key,  # type: int
        parent,  # type: Union[List[Union[Field, InlineFragment]], List[Field]]
        path,  # type: List[Union[int, str]]
        ancestors,  # type: List[Any]
    ):
        fragName = node.name.value
        fragType = self.context.getFragmentType(fragName)
        if fragType:
            self.types.add(fragType)
