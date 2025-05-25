const sinon = require("sinon");
const { v4: uuidv4 } = require("uuid");

module.exports = {
  mockSuccessfulAuthentication: () => {
    return {
      session: {
        token: uuidv4(),
      },
      accounts: [
        {
          accountId: "demo-account-123",
          accountType: "DEMO",
        },
      ],
    };
  },

  mockFailedAuthentication: () => {
    return {
      error: {
        code: "AUTH_FAILED",
        message: "Invalid credentials",
      },
    };
  },

  mockExpiredToken: () => {
    return {
      error: {
        code: "TOKEN_EXPIRED",
        message: "Session token expired",
      },
    };
  },
};
