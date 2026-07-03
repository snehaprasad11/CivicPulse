let
    Source = Csv.Document(
        Web.Contents("http://127.0.0.1:8000/exports/mitigation-results.csv"),
        [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"audit_id", type text},
            {"protected_attribute", type text},
            {"strategy", type text},
            {"accuracy", type number},
            {"demographic_parity_difference", type number},
            {"equal_opportunity_difference", type number},
            {"notes", type text}
        }
    )
in
    ChangedTypes
