# fastapi-mongo-backend-challenge  
  
# Instructions to run  
- Clone the reposioty  
- navigate to the folder  
  ```cd fastapi-mongo-backend-challenge```  
    
- create a virtual environment  
  ```virtualenv venv -p python3.8```  
    
- Activate the virtual environment  
  ```source venv/bin/activate```  
    
- Install all the requirements  
  ```pip3 install -r requirements.txt```  
  
- Run the application  
  ```uvicorn app.main:app --reload```  
  
- Access the swagger documentation  
  ```127.0.0.0:8000/docs```  
  
- Alternatively, you can build a docker image   
  ```sudo docker build -t {image_name} .```  
    
- Run the image  
  ```sudo docker run -d --name {container_name} -p {port}:8000 {image_name}```  
  

```Voila!```
