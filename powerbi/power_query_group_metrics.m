let
    Source = Csv.Document(
        Web.Contents("http://127.0.0.1:8000/exports/group-metrics.csv"),
        [Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"audit_id", type text},
            {"protected_attribute", type text},
            {"group", type text},
            {"count", Int64.Type},
            {"selection_rate", type number},
            {"true_positive_rate", type number},
            {"false_positive_rate", type number},
            {"accuracy", type number}
        }
    )
in
    ChangedTypes
