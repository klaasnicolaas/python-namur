# Complete parking collections

[Back to the README](../README.md)

Use `parking_collection()` when a consumer needs the whole selected parking dataset. The existing `parking_spaces(limit=...)` method remains available for capped queries.

```python
async with ODPNamur() as client:
    collection = await client.parking_collection(ParkingType.PMR, max_records=10000)
    for record in collection.records:
        print(record.id, record.source_attributes)
```

Every successful `ParkingCollection` uses the same result fields:

| Field | Type | Meaning |
| :---- | :--- | :------ |
| `records` | `list[ParkingSpot]` | Every record in the selected source dataset |
| `total_count` | `int` | Source-reported count, equal to the number of returned records |
| `pages_fetched` | `int` | Number of successfully fetched record pages, including an empty response |
| `source_version` | `str \| None` | Opaque source revision; Namur supplies its genuine `data_processed` timestamp |
| `complete` | `bool` | Always `True` on success; failures raise an exception |

The client checks page sizes, reported counts and nonblank unique original identifiers across every page. It compares the dataset processing revision before and after collection and retains original source fields in each record's `source_attributes`. A valid empty selection returns a complete collection with zero records. Source errors, missing revision metadata, changing counts or revisions, incomplete pages and invalid or duplicate records raise an exception instead of returning a partial collection.

`max_records` is a safety ceiling, never a truncation limit. It must be a positive integer (not a boolean) at most 10,000, matching the supported Opendatasoft search range. A larger selection raises `ODPNamurResultsError`; an invalid ceiling raises `ValueError` before any request.

These checks detect observed inconsistencies. Namur does not provide a transactional snapshot token: an unchanged processing timestamp cannot prove that records were immune to concurrent source updates.
