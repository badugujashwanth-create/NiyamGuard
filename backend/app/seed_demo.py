from app.services.platform_store import reset_demo_store


def main() -> None:
    store = reset_demo_store(persist=True)
    print(
        "Seeded NiyamGuard government-core demo data: "
        f"{len(store.circulars)} circulars, "
        f"{len(store.verified_rules)} verified rules, "
        f"{len(store.connected_systems)} connected systems."
    )


if __name__ == "__main__":
    main()
