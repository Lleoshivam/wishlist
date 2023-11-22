from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Wishlist(BaseModel):
    user_id: int
    product_url: str
    product_name: str


while True:
    try:
        # conn = psycopg2.connect(host='localhost', database='wishlist',
        #                         user='postgres', password='admin', cursor_factory=RealDictCursor)
        conn = psycopg2.connect(host='database-2.cbzsyhmrotmw.us-east-1.rds.amazonaws.com', database='wishlist',
                                user='postgres', password='adminadmin', port='5432', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connected Succesfully")
        break
    except Exception as error:
        print("Connection Failed")
        print("Error:", error)
        time.sleep(2)


@app.get("/")
def root():
    return "hello World"


@app.get("/wishlists")
def get_all_wishlist():
    cursor.execute("""SELECT * FROM wishlist""")
    wishlist = cursor.fetchall()
    return wishlist


@app.get("/wishlists/{user_id}")
async def get_wishlist(user_id: int, response: Response):
    cursor.execute(
        """SELECT * FROM wishlist WHERE user_id= %s""", (str(user_id),))
    wishlist = cursor.fetchall()
    if not wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="userid not found")

    return wishlist


@app.post("/wishlists", status_code=status.HTTP_201_CREATED)
def add_to_wishlist(payLoad: Wishlist):
    cursor.execute(
        """INSERT INTO wishlist (user_id, product_url, product_name) VALUES (%s, %s, %s) RETURNING *""", (payLoad.user_id, payLoad.product_url, payLoad.product_name))
    wishlist = cursor.fetchone()
    conn.commit()
    return wishlist


@app.post("/wishlists/check")
def is_product_present_in_wishlist(payLoad: Wishlist):
    cursor.execute("""SELECT * FROM wishlist WHERE user_id=%s and product_url=%s and product_name=%s""",
                   (str(payLoad.user_id), payLoad.product_url, payLoad.product_name))
    wishlist = cursor.fetchone()
    if wishlist:
        return True
    else:
        return False


@app.delete("/wishlists/{wishlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(wishlist_id: int):
    cursor.execute("""DELETE FROM wishlist WHERE id= %s RETURNING * """,
                   (str(wishlist_id),))
    deleted_wishlist = cursor.fetchone()

    conn.commit()

    if not deleted_wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="record not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
