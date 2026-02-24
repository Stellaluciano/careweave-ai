from packages.retrieval.store import default_backend


def main() -> None:
    backend = default_backend()
    total = backend.index_corpus()
    print(f"Indexed chunks: {total}")


if __name__ == "__main__":
    main()
