class PAOQueries:
    AQL_UPSERT_DOC="""
        UPSERT {{ {key_attrs} }}
        INSERT {{ {insert_attrs} }}
        UPDATE {{ {update_attrs} }}
        IN @@collection OPTIONS {{ keepNull: false }}
        RETURN NEW
    """

    # INSERT AQL with created_at set:
    # attrs and keyattrs in format "KEY1:VAL1, KEY2:VAL2..."
    AQL_INSERT_DOC="""
        INSERT {{ {insert_attrs} }} INTO @@collection
        RETURN NEW
    """

    AQL_INSERT_DOCS = """
        FOR doc IN @docs
            INSERT doc INTO @@collection 
    """

    AQL_REMOVE_BY_ATTRS="""
        FOR doc in @@collection
            {lookup_filter}
            REMOVE doc IN @@collection
    """
    AQL_QUERY_ALL="""
        FOR doc in @@collection
          SORT {sort_attrs}
          RETURN doc
    """

    AQL_QUERY_BY_ATTRS="""
        FOR doc in @@collection
          {lookup_filter}
          {sort_by}
          RETURN doc
    """

    # Lookup associated edges:
    AQL_QUERY_RELATED_EDGES = """
        FOR doc IN @@collection
          {lookup_filter}
          FOR edge IN @@edge_collection
            FILTER edge._from == doc._id
            RETURN edge
    """

    # Lookup associated vertices through edges:
    AQL_QUERY_RELATED_VERTICES = """
        FOR doc IN @@collection
          {lookup_filter}
          FOR edge IN @@edge_collection
            FILTER edge._from == doc._id
            FOR rel_doc IN @@association_collection
              FILTER rel_doc._id == edge._to
                RETURN rel_doc
    """
