from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="NEXTLINE",
    settings_files=["settings.toml"],
)
