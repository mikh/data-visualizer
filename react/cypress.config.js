import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://127.0.0.1:5173",
    supportFile: "cypress/support/e2e.js",
    specPattern: "cypress/e2e/**/*.cy.{js,jsx}",
    viewportWidth: 1280,
    viewportHeight: 900,
    setupNodeEvents(on) {
      on("task", {
        log(message) {
          console.log(message);
          return null;
        },
      });
    },
  },
});
