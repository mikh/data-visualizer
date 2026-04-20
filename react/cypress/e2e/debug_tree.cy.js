describe("Debug tree", () => {
  it("logs tree structure", () => {
    cy.visit("/");
    cy.intercept("POST", "**/api/tree").as("treeApi");
    cy.wait("@treeApi", { timeout: 10000 }).then((interception) => {
      cy.task("log", "API status: " + interception.response.statusCode);
      cy.task("log", "API body: " + JSON.stringify(interception.response.body).substring(0, 500));
    });
    cy.get("[data-cy='tree-header']", { timeout: 10000 }).should("exist");
    cy.wait(2000);
    cy.get("body").then(($body) => {
      cy.task("log", "tree-folder count: " + $body.find("[data-cy='tree-folder']").length);
      cy.task("log", "tree-file count: " + $body.find("[data-cy='tree-file']").length);
      cy.task(
        "log",
        "tree-body HTML: " +
          ($body.find("[data-cy='tree-body']").html() || "NOT FOUND").substring(0, 1000)
      );
    });
  });
});
