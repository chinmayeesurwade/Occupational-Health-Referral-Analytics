// Power BI: Blank query > Advanced Editor. Name query Referrals.
let
    Source = PostgreSQL.Database("localhost:5432", "occupational_health"),
    Referrals = Source{[Schema="public",Item="reporting_referrals"]}[Data]
in
    Referrals
