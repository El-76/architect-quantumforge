import json
import sys


def load_jsonl(path):
    data = {}

    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            obj = json.loads(line)

            query = obj.get("query")
            answer = obj.get("answer")

            if query is None:
                raise ValueError(f"{path}:{line_no}: missing 'query'")

            data[query] = answer

    return data


def main():
    if len(sys.argv) != 3:
        print(
            f"Usage: {sys.argv[0]} candidate.jsonl reference.jsonl",
            file=sys.stderr,
        )
        sys.exit(1)

    candidate_file = sys.argv[1]
    reference_file = sys.argv[2]

    candidate = load_jsonl(candidate_file)
    reference = load_jsonl(reference_file)

    common_queries = candidate.keys() & reference.keys()

    for query in common_queries:
        result = {
            "question": query,
            "candidate_answer": candidate[query],
            "reference_answer": reference[query],
        }

        print(
            json.dumps(
                result,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
