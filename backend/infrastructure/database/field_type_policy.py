from dataclasses import dataclass

from sqlalchemy import MetaData, DateTime

from backend.infrastructure.database.mixins import BusinessEntityMixin


@dataclass(frozen=True,slots=True)
class FieldTypeViolation:
    table:str
    column:str
    message:str

    def __str__(self) -> str:
        return f"{self.table}.{self.column}: {self.message}"


def check_field_types(metadata:MetaData) -> list[FieldTypeViolation]:

    violations: list[FieldTypeViolation] = []
    required_fields = BusinessEntityMixin.__annotations__

    for table in metadata.tables.values():
        if table.info.get("skip_field_type_policy", False):
            continue

        for field_name in required_fields:
            column = table.columns.get(field_name)

            if column is None:
                violations.append(
                    FieldTypeViolation(
                        table=table.fullname,
                        column=field_name,
                        message="Required field is missing",
                    )
                )
                continue

            if column.nullable:
                violations.append(
                    FieldTypeViolation(
                        table=table.fullname,
                        column=field_name,
                        message="Field must be NOT NULL",
                    )
                )

            if field_name in ("created_at", "updated_at"):
                if not (
                    isinstance(column.type, DateTime)
                    and column.type.timezone
                ):
                    violations.append(
                        FieldTypeViolation(
                            table=table.fullname,
                            column=field_name,
                            message="Field must use a timezone-aware DateTime",
                        )
                    )

            if field_name == "id":
                if (
                    not column.primary_key
                    or len(table.primary_key.columns) != 1
                ):
                    violations.append(
                        FieldTypeViolation(
                            table=table.fullname,
                            column=field_name,
                            message="Field must be the sole primary key",
                        )
                    )

                if column.autoincrement is not False:
                    violations.append(
                        FieldTypeViolation(
                            table=table.fullname,
                            column=field_name,
                            message="Snowflake ID requires autoincrement=False",
                        )
                    )

                if (
                    column.identity is not None
                    or column.server_default is not None
                ):
                    violations.append(
                        FieldTypeViolation(
                            table=table.fullname,
                            column=field_name,
                            message="Snowflake ID must be application-generated",
                        )
                    )

    return violations


def validate_field_types(metadata: MetaData) -> None:
    """Raise an error if registered table definitions violate conventions."""
    if not metadata.tables:
        raise ValueError(
            "No ORM tables are registered. "
            "Import application ORM models before validation."
        )

    violations = check_field_types(metadata)
    if violations:
        details = "\n".join(f"- {violation}" for violation in violations)
        raise ValueError(f"ORM field validation failed:\n{details}")