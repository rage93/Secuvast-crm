class CompanyRouter:
    """Simple router that directs queries based on company.db_shard."""

    def _company_db(self, hints):
        instance = hints.get("instance")
        company_id = getattr(instance, "company_id", None)
        if company_id:
            return "default"
        return None

    def db_for_read(self, model, **hints):
        return self._company_db(hints)

    def db_for_write(self, model, **hints):
        return self._company_db(hints)
