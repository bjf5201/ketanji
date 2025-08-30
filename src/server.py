import os.path
from contextlib import asynccontextmanager as acm

from fastapi import FastAPI, Depends
from pyright import List, Annotated, Tuple
from sqlmodel import SQLModel, create_engine, Field, Session, select

"""Sets the base path for the user's home directory and constructs
the path for the SQLite database file"""
base_path = os.path.expanduser('~')
db_path = os.path.join(base_path, '.ketanji', 'ketanji.sqlite3')

"""Configures SQLite connection arguments & creates a database engine"""
connect_args = {"check_same_thread": False}
engine = create_engine(f'sqlite:///{db_path}', connect_args=connect_args)

class Plugin(SQLModel, table=True):
    """Defines the Plugin model for storing plugin information in the database"""
    name: str = Field(primary_key=True)
    description: str
    config_data: str
    is_enabled: bool


    def create_db_tables(self):
        """Method for creating database tables from models"""
        SQLModel.metadata.create_all(engine)

    def get_session():
        """Dependency for getting a database session"""
        with Session(engine) as session:
            yield session

    """Type alias for a session dependency"""
    SessionDep = Annotated[Session, Depends(get_session)]

    @acm
    async def lifespan(_: FastAPI):
        # Async context manager for lifespan events; creates tables before serving requests
        create_db_tables()
        yield

"""Creates the FastAPI app instance with the lifespan handler"""
app = FastAPI(lifespan=lifespan)

@app.get("/plugins", response_model=List[Plugin])
async def get_plugin_list(session: SessionDep) -> List:
    """GET endpoint to list all plugins, returns 404 if no plugins found"""
    plugins = session.exec(select(Plugin)).all()
    if not plugins:
        raise HTTPException(status_code=404, detail="No plugins found")
    return plugins


@app.post("/plugins", response_model=Plugin)
async def create_plugin(plugin: Plugin, session: SessionDep) -> Plugin:
    """POST endpoint to create a new plugin entry, returns 400 if plugin data is invalid"""
    plugin_validated = Plugin.model_validate(plugin)
    if not plugin_validated:
        raise HTTPException(status_code=400, detail="Invalid plugin data")
    session.add(plugin_validated)
    session.commit()
    session.refresh(plugin_validated)
    return plugin_validated


@app.get("plugins/{plugin_name}", response_model=Plugin)
async def get_plugin_info(plugin_name: str, session: SessionDep) -> Plugin:
    """GET endpoint to fetch a plugin by name, returns 404 if not found"""
    plugin = session.get(Plugin, plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin


@app.put("/plugins/{plugin_name}", response_model=Plugin)
async def update_plugin(plugin_name: str, updated_plugin: Plugin, session: SessionDep) -> Plugin:
    """PUT endpoint to update an existing plugin, returns 404 if plugin not found"""
    plugin_existing = session.get(Plugin, plugin_name) or Plugin(name=plugin_name)
    if not plugin_existing:
        raise HTTPException(status_code=404, detail="Plugin not found")
    plugin_data = updated_plugin.model_dump()
    for key, value in plugin_data.items():
        setattr(plugin_existing, key, value)
    session.add(plugin_existing)
    session.commit()
    session.refresh(plugin_existing)
    return plugin_existing


@app.delete("/plugins/{plugin_name}")
async def delete_plugin(plugin_name: str, session: SessionDep) -> Tuple:
    """DELETE endpoint to remove a plugin by name, returns 404 if plugin not found"""
    plugin = session.get(Plugin, plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    session.delete(plugin)
    session.commit()
    return {"message": "Plugin deleted successfully"}