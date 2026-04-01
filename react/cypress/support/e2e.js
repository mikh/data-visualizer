// Custom command to expand the tree panel by clicking the header (tree is collapsed by default)
Cypress.Commands.add("expandTree", () => {
  cy.get("[data-cy='tree-header']").then(($header) => {
    // Check if tree-body exists (i.e., tree is already expanded)
    const $body = Cypress.$("[data-cy='tree-body']");
    if ($body.length === 0) {
      cy.wrap($header).click();
    }
  });
  cy.get("[data-cy='tree-body']").should("exist");
});

// Custom command to load a file by clicking it in the file tree
Cypress.Commands.add("loadFile", (fileName) => {
  cy.expandTree();
  cy.contains("[data-cy='tree-file']", fileName).within(() => {
    cy.get("[data-cy='tree-file-load']").click();
  });
});

// Custom command to expand a folder in the file tree
Cypress.Commands.add("expandFolder", (folderName) => {
  cy.expandTree();
  cy.contains("[data-cy='tree-folder']", folderName).click();
});
