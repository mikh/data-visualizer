describe("Header", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  context("version display", () => {
    it("displays the app title", () => {
      cy.get("header h1").should("contain", "Data Visualization");
    });

    it("displays the Flask backend version", () => {
      cy.get("header").should("contain", "Flask v");
    });

    it("displays the React version", () => {
      cy.get("header").should("contain", "React v");
    });
  });

  context("attributions modal", () => {
    it("does not show attributions by default", () => {
      cy.contains("Image Attributions").should("not.exist");
    });

    it("shows attributions when button is clicked", () => {
      cy.contains("button", "Attributions").click();
      cy.contains("Image Attributions").should("be.visible");
    });

    it("hides attributions when button is clicked again", () => {
      cy.contains("button", "Attributions").click();
      cy.contains("Image Attributions").should("be.visible");

      cy.contains("button", "Attributions").click();
      cy.contains("Image Attributions").should("not.exist");
    });

    it("displays attribution links", () => {
      cy.contains("button", "Attributions").click();
      cy.contains("Visualization icons created by juicy_fish").should(
        "be.visible"
      );
    });
  });
});
