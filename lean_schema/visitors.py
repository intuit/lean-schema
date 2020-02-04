from graphql.language.visitor import Visitor


class AllTypesVisitor(Visitor):
    """
    Visitor to hoover up all referenced Types in a Query and collect them as a single Set

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
        # if getattr(node, 'value', None) == "id" or getattr(node, 'name', None) == "id":
        #     from ipdb import set_trace
        #     set_trace()
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
        print("enter_FragmentSpread")
        fragName = node.name.value
        fragType = self.context.getFragmentType(fragName)
        if fragType:
            self.types.add(fragType)
