# #The goal of this assignment is to demonstrate your existing Python3 skills and how you can
# create a minimal API using FastAPI.

#Create an address book application where API users can create, update and delete addresses.
# The address should:
# - contain the coordinates of the address.
# - be saved to an SQLite database.
# - be validated
# API Users should also be able to retrieve the addresses that are within a given distance and
# location coordinates.
# Important: The application does not need a GUI. (Built-in FastAPI’s Swagger Doc is sufficient)

#The application should be written in Python 3.8 and use FastAPI.
# The application should be able to run on Linux and Windows.

import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from math import sin, cos, sqrt, atan2, radians
import uvicorn

app = FastAPI()

class Address(BaseModel):
	name: str
	address: str
	city: str
	state: str
	zip: str
	latitude: float
	longitude: float

class AddressUpdate(BaseModel):
	name: Optional[str]
	address: Optional[str]
	city: Optional[str]
	state: Optional[str]
	zip: Optional[str]
	latitude: Optional[float]
	longitude: Optional[float]

class AddressDistance(BaseModel):
	latitude: float
	longitude: float
	distance: float

@app.get("/")
def read_root():
	return {"Hello": "World"}

@app.get("/address")
def read_address():
	conn = sqlite3.connect('address.db')
	c = conn.cursor()
	c.execute("SELECT * FROM address")
	rows = c.fetchall()
	conn.close()
	return rows

@app.get("/address/{address_id}")
def read_address(address_id: int):
	conn = sqlite3.connect('address.db')
	c = conn.cursor()
	c.execute("SELECT * FROM address WHERE id=?", (address_id,))
	row = c.fetchone()
	conn.close()
	if row is None:
		raise HTTPException(status_code=404, detail="Address not found")
	return row

@app.post("/address")
def create_address(address: Address):
	conn = sqlite3.connect('address.db')
	c = conn.cursor()
	c.execute("INSERT INTO address VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (address.name, address.address, address.city, address.state, address.zip, address.latitude, address.longitude))
	conn.commit()
	conn.close()
	return {"message": "Address created successfully"}

@app.put("/address/{address_id}")
def update_address(address_id: int, address: AddressUpdate):
	conn = sqlite3.connect('address.db')
	c = conn.cursor()
	c.execute("SELECT * FROM address WHERE id=?", (address_id,))
	row = c.fetchone()
	if row is None:
		raise HTTPException(status_code=404, detail="Address not found")
	c.execute("UPDATE address SET name=?, address=?, city=?, state=?, zip=?, latitude=?, longitude=? WHERE id=?", (address.name, address.address, address.city, address.state, address.zip, address.latitude, address.longitude, address_id))
	conn.commit()
	conn.close()
	return {"message": "Address updated successfully"}

@app.delete("/address/{address_id}")
def delete_address(address_id: int):
	conn = sqlite3.connect('address.db')
	c = conn.cursor()
	c.execute("SELECT * FROM address WHERE id=?", (address_id,))
	row = c.fetchone()
	if row is None:
		raise HTTPException(status_code=404, detail="Address not found")
	c.execute("DELETE FROM address WHERE id=?", (address_id,))
	conn.commit()
	conn.close()
	return {"message": "Address deleted successfully"}

@app.post("/address/distance")
def distance_address(address: AddressDistance):
	conn = sqlite3.connect('address.db')
	c = conn.cursor()
	c.execute("SELECT * FROM address")
	rows = c.fetchall()
	conn.close()
	if rows is None:
		raise HTTPException(status_code=404, detail="Address not found")
	lat1 = radians(address.latitude)
	lon1 = radians(address.longitude)
	addresses = []
	for row in rows:
		lat2 = radians(row[5])
		lon2 = radians(row[6])
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
		c = 2 * atan2(sqrt(a), sqrt(1 - a))
		distance = 6373.0 * c
		if distance <= address.distance:
			addresses.append(row)
	return addresses

if __name__ == "__main__":
	uvicorn.run(app, host="localhost", port=8000)
