// INFO: This file contains the API calls to the server

export async function getDB(): Promise<any> {
    console.log("getDB() called on frontend!");
    const data = fetch('http://localhost:5000/api/getdb')
        /* fetch('http://localhost:3000/') */
        .then(response => response.json())
        .then(data => console.log(data));
    return data;
}

export async function getStocksFromServer(): Promise<any> {
    console.log("getStocks() called on frontend!");
    const response = await fetch('http://localhost:5000/api/stocks/apple');
    const jsonData = await response.json();
    // console.log(response);
    console.log(jsonData);
    return jsonData;
}

// INFO: Requests all the current bids (this includes the user's own bids) from the server
// @param credential: The user's email and sub
export async function getBidsFromServer(credential: { email: string | Blob; sub: string | Blob; }): Promise<any> {
    console.log("getBidsFromServer() called on frontend!");
    console.log(credential);

    const formData = new FormData();
    formData.append('email', credential.email);
    formData.append('sub', credential.sub);
    const data = fetch("http://localhost:5000/api/stocks/bids", {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log("Whole response: ");
            console.log(data);

            console.log("Status code:" + data.status);
            console.log("Message: " + data.message);
            console.log(data.data);

            const status = data.status;

            switch (status) {
                case 0:
                    {
                        console.log("Get bids success on existing user!");
                        return data;
                    }
                case 1:
                    {
                        console.log("Couldn't fetch bids, is the server running?");
                        return null;
                    }
            }
        }
        );
    return data;
}

// INFO: Sends a login request to the server and returns the response to the caller (most likely frontend)
// @param credential: The user's email and sub
export async function sendLogin(credential: { email: string | Blob; sub: string, first_name: string, last_name: string | Blob; }): Promise<any> {
    console.log("sendLogin() called on frontend!");
    console.log("Credentials:");
    console.log(credential);

    const formData = new FormData();
    formData.append('email', credential.email);
    formData.append('sub', credential.sub);
    formData.append('first_name', credential.first_name);
    formData.append('last_name', credential.last_name);
    const data = fetch("http://localhost:5000/api/auth/login", {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log("Whole response: " + data);
            const status = data.split(',')[0]
            console.log("status is \"" + status + "\"");

            // TODO: Use response codes instead of strings
            switch (status) {
                case "success_existingUser":
                    {
                        console.log("Login successful on existing user!");
                        return "hululululu";
                    }
                case "success_newUser":
                    {
                        console.log("Login successful on new user!"); break;
                    }
                case "error_newUser":
                    {
                        console.log("Login failed on new user!"); break;
                    }
                case "error_existingUser":
                    {
                        console.log("Login failed on existing user!"); break;
                    }
            }
        }
        );
    return data;
}

// INFO: Sends a logout request to the server and returns the response to the caller (most likely frontend)
// @param credential: The user's email and sub
// @return: true if the logout was successful, false otherwise
export async function sendLogout(credential: { email: string | Blob; sub: string | Blob; }): Promise<any> {
    console.log("sendLogout() called on frontend!");
    console.log(credential);

    const formData = new FormData();
    formData.append('email', credential.email);
    formData.append('sub', credential.sub);
    const data = fetch("http://localhost:5000/api/auth/logout", {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log("Whole response: " + data);
            const status = data.split(',')[0]
            console.log("status is \"" + status + "\"");

            switch (status) {
                case "success_existingUser":
                    {
                        console.log("Logout successful on existing user!");
                        return true;
                    }
                // FIXME: Handle logout errors
                /* case "success_newUser": */
                /*     { */
                /*         console.log("Login successful on new user!"); break; */
                /*     } */
                /* case "error_newUser": */
                /*     { */
                /*         console.log("Login failed on new user!"); break; */
                /*     } */
                /* case "error_existingUser": */
                /*     { */
                /*         console.log("Login failed on existing user!"); break; */
                /*     } */
            }
        }
        );
    return data;
}

// INFO: Sends a bid addition request to the server and returns the response to the caller (most likely frontend)
// @param credential: The user's email and sub
// @param bidData: Added bid data
export async function sendBidAdditionRequest(credential: { email: string | Blob; sub: string | Blob; }, bidData: { user_id: string | Blob; stock_id: string | Blob; amount: string | Blob; price: string | Blob; }): Promise<any> {
    console.log("sendBidAdditionRequest() called on frontend!");
    console.log(credential);

    const formData = new FormData();
    // FIXME: we don't really need to send the email here, the sub (used as user id) is enough
    formData.append('email', credential.email);
    formData.append('sub', credential.sub);
    // INFO: We can't send the bidData object as is, so we need to send the individual fields
    /* formData.append('bidData.id', bidData.id); // INFO:Setting the id is done on the server */
    formData.append('bidData.user_id', bidData.user_id);
    formData.append('bidData.stock_id', bidData.stock_id);
    formData.append('bidData.amount', bidData.amount);
    formData.append('bidData.price', bidData.price);

    const data = fetch("http://localhost:5000/api/stocks/bid", {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log("Whole response: " + data);
            const status = data.split(',')[0]
            console.log("status is \"" + status + "\"");

            switch (status) {
                case "success_existingUser":
                    {
                        console.log("Able to add bid on existing user!");
                        return true;
                    }
                // FIXME: Handle logout errors
                /* case "success_newUser": */
                /*     { */
                /*         console.log("Login successful on new user!"); break; */
                /*     } */
                /* case "error_newUser": */
                /*     { */
                /*         console.log("Login failed on new user!"); break; */
                /*     } */
                /* case "error_existingUser": */
                /*     { */
                /*         console.log("Login failed on existing user!"); break; */
                /*     } */
            }
        }
        );
    return data;
}

// INFO: Sends a sell addition request to the server and returns the response to the caller (most likely frontend)
// @param credential: The user's email and sub
// @param sellData: Added sell data
export async function sendSellAdditionRequest(credential: { email: string | Blob; sub: string | Blob; }, sellData: { user_id: string | Blob; stock_id: string | Blob; amount: string | Blob; price: string | Blob; }): Promise<any> {
    console.log("sendSellAdditionRequest() called on frontend!");
    console.log(credential);

    const formData = new FormData();
    // FIXME: we don't really need to send the email here, the sub (used as user id) is enough
    formData.append('email', credential.email);
    formData.append('sub', credential.sub);
    // INFO: We can't send the sellData object as is, so we need to send the individual fields
    /* formData.append('sellData.id', sellData.id); // INFO:Setting the id is done on the server */
    formData.append('sellData.user_id', sellData.user_id);
    formData.append('sellData.stock_id', sellData.stock_id);
    formData.append('sellData.amount', sellData.amount);
    formData.append('sellData.price', sellData.price);

    const data = fetch("http://localhost:5000/api/stocks/sell", {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log("Whole response: " + data);
            const status = data.split(',')[0]
            console.log("status is \"" + status + "\"");

            switch (status) {
                case "success_existingUser":
                    {
                        console.log("Able to add sell on existing user!");
                        return true;
                    }
                // FIXME: Handle logout errors
                /* case "success_newUser": */
                /*     { */
                /*         console.log("Login successful on new user!"); break; */
                /*     } */
                /* case "error_newUser": */
                /*     { */
                /*         console.log("Login failed on new user!"); break; */
                /*     } */
                /* case "error_existingUser": */
                /*     { */
                /*         console.log("Login failed on existing user!"); break; */
                /*     } */
            }
        }
        );
    return data;
}
