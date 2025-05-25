```markdown
  # Capital Bot API Documentation

  ## Overview
  This API provides integration with Capital.com for trading and account management.

  ## Endpoints

  ### `POST /api/authenticate`
  - **Description**: Authenticate with Capital.com using API credentials.
  - **Request Body**:
    ```json
    {
      "identifier": "string",
      "password": "string",
      "apiKey": "string"
    }
    ```
  - **Response**:
    ```json
    {
      "success": boolean,
      "message": string,
      "sessionToken": string
    }
    ```

  ### `GET /api/account-info`
  - **Description**: Retrieve account information from Capital.com.
  - **Response**:
    ```json
    {
      "accountId": string,
      "balance": number,
      "currency": string
    }
    ```
  ```