const { expect } = require("chai");
const { authenticate } = require("../../src/api/authenticate");
const { v4: uuidv4 } = require("uuid");

describe("Authentication API", () => {
  describe("authenticate function", () => {
    it("should return a session token on successful authentication", async () => {
      const credentials = {
        identifier: "test-user",
        password: "test-password",
        apiKey: "test-api-key",
      };

      const result = await authenticate(credentials);
      expect(result).to.haveOwnProperty("sessionToken");
      expect(result.sessionToken).to.be.a("string");
    });

    it("should return an error on invalid credentials", async () => {
      const credentials = {
        identifier: "invalid-user",
        password: "invalid-password",
        apiKey: "invalid-api-key",
      };

      try {
        await authenticate(credentials);
        throw new Error("Expected error not thrown");
      } catch (error) {
        expect(error.message).to.include("Invalid credentials");
      }
    });

    it("should handle missing credentials", async () => {
      try {
        await authenticate({});
        throw new Error("Expected error not thrown");
      } catch (error) {
        expect(error.message).to.include("Missing required credentials");
      }
    });

    it("should handle invalid API key format", async () => {
      const credentials = {
        identifier: "test-user",
        password: "test-password",
        apiKey: "invalid-api-key-format",
      };

      try {
        await authenticate(credentials);
        throw new Error("Expected error not thrown");
      } catch (error) {
        expect(error.message).to.include("Invalid API key format");
      }
    });

    it("should handle rate limiting", async () => {
      const credentials = {
        identifier: "test-user",
        password: "test-password",
        apiKey: "test-api-key",
      };

      // Simulate multiple failed attempts
      for (let i = 0; i < 5; i++) {
        try {
          await authenticate(credentials);
        } catch (error) {
          // Intentionally ignore errors
        }
      }

      try {
        await authenticate(credentials);
        throw new Error("Expected error not thrown");
      } catch (error) {
        expect(error.message).to.include("Too many failed attempts");
      }
    });

    it("should handle token expiration", async () => {
      const credentials = {
        identifier: "test-user",
        password: "test-password",
        apiKey: "test-api-key",
      };

      const result = await authenticate(credentials);
      expect(result).to.haveOwnProperty("sessionToken");

      // Simulate token expiration
      global.capitalSession = {
        token: result.sessionToken,
        expiresAt: new Date().getTime() - 10000, // Expired 10 seconds ago
      };

      try {
        await authenticate(credentials);
        throw new Error("Expected error not thrown");
      } catch (error) {
        expect(error.message).to.include("Session token expired");
      }
    });
  });
});
