class PAOQueries:
    AQL_UPSERT_DOC="""
        UPSERT {{ {key_attrs} }}
        INSERT {{ {insert_attrs}, created_at: DATE_NOW() }}
        UPDATE {{ {update_attrs}, updated_at: DATE_NOW() }}
        IN @@collection OPTIONS {{ keepNull: false }}
        RETURN NEW
      """

    # INSERT AQL with created_at set:
    # attrs and keyattrs in format "KEY1:VAL1, KEY2:VAL2..."
    AQL_INSERT_DOC="""
        INSERT {{ {insert_attrs}, created_at: DATE_NOW(), updated_at: DATE_NOW() }} INTO @@collection
        RETURN NEW
    """

    AQL_QUERY_BY_ATTRS="""
        FOR doc in @@collection
          FILTER {lookup_filter}
          RETURN doc
      """

      # Lookup associated docs
    AQL_QUERY_RELATED = """
        FOR doc IN @@collection
          FILTER {lookup_filter}
          FOR edge IN @@edge_collection
            FILTER edge._from == doc._id
            FOR rel_doc IN @@association_collection
              FILTER rel_doc._id == edge._to
                RETURN rel_doc
      """
