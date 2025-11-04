from sqlalchemy.orm import Session
from fastapi import FastAPI,Depends, HTTPException, status
from fastapi.responses import JSONResponse
from schema import ToDoSchema, UpdateToDoSchema
from models import ToDoModel
from database_config import Base, get_db, engine

Base.metadata.create_all(bind=engine)


app = FastAPI()

@app.post('/create/task')
def Create_Task(task: ToDoSchema, db: Session=Depends(get_db)):
    new_task = ToDoModel(**(task.dict()))
    if new_task:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        raise HTTPException(
            status_code=status.HTTP_201_CREATED,
            detail="task created sucessfully"
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="SomeThing Went Wrong"
        )



@app.get('/all/task')
def get_all_tasks(db: Session=Depends(get_db)):
    tasks = db.query(ToDoModel).all()
    if tasks:
        return{'message':'data fetched sucessfully', 'data':tasks}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Something went wrong'
    )


@app.get('/task/{t_id}')
def single_Task(t_id: int, db: Session=Depends(get_db)):
    task = db.query(ToDoModel).filter(ToDoModel.id==t_id).first()
    
    if task:
        return {'message':'data fetched', 'data':task}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Something went wrong'
    )


@app.get('/task-status/{task_status}')
def inCompleted_tasks(task_status: bool,db: Session=Depends(get_db)):
    tasks = db.query(ToDoModel).filter(ToDoModel.status==task_status).all()

    if tasks:
        return {'message':'data fetched', 'data':tasks}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='something went wrong'
    )


@app.delete('/delete-task/{t_id}')
def dete_task(t_id: int, db: Session=Depends(get_db)):
    task = db.query(ToDoModel).filter(ToDoModel.id==t_id).first()
    
    if task:
        db.delete(task)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail='task deleted'
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="something went wrong"
        )


@app.put('/update-task/{t_id}')
def update_task(t_id: int, UTask:UpdateToDoSchema, db: Session=Depends(get_db)):
    task = db.query(ToDoModel).filter(ToDoModel.id==t_id).first()
    
    if task:
        for key, value in UTask.dict(exclude_none=True).items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)
        raise HTTPException(
            status_code=status.HTTP_201_CREATED,
            detail="task updated"
        )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content="something went wronk"
    )