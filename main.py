from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent import Agent  # Import the Agent class from agent.py

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update the origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/register-agent")
def register_agent(url: str):
    """
    Endpoint to call the Agent's form extraction method.
    Provide a URL as a query parameter.
    """
    try:
        # Create an instance of the Agent class
        agent_instance = Agent()

        # Use the run method to process the URL
        response = agent_instance.run(url)

        return {"message": "Form fields extracted successfully.", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    

############################################################################
#                    DESKTOP AGENT WALLET ENDPOINT
############################################################################

@app.get("/wallet")
def get_metamax_balance():
    """
    Endpoint to retrieve the MetaMask wallet balance using the built-in read_balance() method.
    """
    try:
        reader = MetaMaskReader(
            extension_path=r"C:\Users\dmart\AppData\Local\Microsoft\Edge\User Data\Default\Extensions\ejbalbakoplchlghecdalmeeeajnimhm",
            metamask_password="Planning1!",
            extension_id="ejbalbakoplchlghecdalmeeeajnimhm"
        )
        # read_balance() sets up the browser, unlocks the wallet, fetches balance, and quits
        balance = reader.read_balance()
        return {"balance": balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#########################################################################
#                            E-SHOP UTILS
#########################################################################

# EP1: pick food
@app.post("/pick-food")
def pick_food(selected_food: List[str]):
    valid_foods = ['mango', 'rice', 'kiwi']
    invalid_selections = [food for food in selected_food if food not in valid_foods]

    if invalid_selections:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid selection(s): {', '.join(invalid_selections)}"
        )

    return {"message": "Food selection successful.", "selected": selected_food}

# EP2: payment endpoint
class PaymentDetails(BaseModel):
    card_number: str = Field(..., example="4111111111111111")
    expiry_date: str = Field(..., example="12/25")
    cvv: str = Field(..., example="123")

@app.post("/payment")
def process_payment(payment_details: PaymentDetails):
    if len(payment_details.card_number) != 16 or not payment_details.card_number.isdigit():
        raise HTTPException(status_code=400, detail="Invalid card number.")
    if len(payment_details.cvv) != 3 or not payment_details.cvv.isdigit():
        raise HTTPException(status_code=400, detail="Invalid CVV.")

    return {"message": "Payment processed successfully.", "details": payment_details.dict()}