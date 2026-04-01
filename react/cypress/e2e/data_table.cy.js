describe("Data Table", () => {
  beforeEach(() => {
    cy.visit("/");
    // Load test-file-1 which is a CSV with data
    cy.expandTree();
    cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
    cy.loadFile("test-file-1");
  });

  context("table rendering", () => {
    it("displays the raw data section header with row count", () => {
      cy.contains("button", "Raw Data").should("be.visible");
      cy.contains("button", "Raw Data").should("contain", "2 rows");
    });

    it("is collapsed by default", () => {
      cy.contains("Showing").should("not.exist");
    });

    it("expands when the header is clicked", () => {
      cy.contains("button", "Raw Data").click();
      cy.contains("Showing").should("be.visible");
    });

    it("collapses when the header is clicked again", () => {
      cy.contains("button", "Raw Data").click();
      cy.contains("Showing").should("be.visible");

      cy.contains("button", "Raw Data").click();
      cy.contains("Showing").should("not.exist");
    });
  });

  context("table content", () => {
    beforeEach(() => {
      cy.contains("button", "Raw Data").click();
    });

    it("displays column headers", () => {
      // test-file-1.csv has headers: column-1, column-2
      cy.get("table th").should("contain", "column-1");
      cy.get("table th").should("contain", "column-2");
    });

    it("displays data rows", () => {
      // test-file-1.csv has rows: [value-1, value-2], [value-3, value-4]
      cy.contains("td", "value-1").should("be.visible");
      cy.contains("td", "value-2").should("be.visible");
      cy.contains("td", "value-3").should("be.visible");
      cy.contains("td", "value-4").should("be.visible");
    });

    it("shows the correct row count", () => {
      cy.contains("Showing 2 of 2 rows").should("be.visible");
    });
  });

  context("JSON file data", () => {
    it("does not display a data table for JSON file data (non-array)", () => {
      cy.loadFile("test-file-2");
      cy.contains("h1", "test-file-2").should("be.visible");
      // JSON data is an object, not an array, so DataTable should not render
      cy.contains("button", "Raw Data").should("not.exist");
    });
  });
});
