describe("File Tree", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  context("tree loading", () => {
    it("displays the tree header", () => {
      cy.get("[data-cy='tree-header']").should("contain", "Visualization Files");
    });

    it("renders the top-level folders", () => {
      cy.expandTree();
      cy.get("[data-cy='tree-folder']").should("have.length.at.least", 3);
      cy.contains("[data-cy='tree-folder']", "test-folder-1").should("exist");
      cy.contains("[data-cy='tree-folder']", "test-folder-2").should("exist");
      cy.contains("[data-cy='tree-folder']", "test-folder-3").should("exist");
    });

    it("renders root-level files", () => {
      cy.expandTree();
      cy.contains("[data-cy='tree-file']", "test-file-2").should("exist");
    });
  });

  context("folder navigation", () => {
    it("expands a folder to show its children", () => {
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.contains("[data-cy='tree-file']", "test-file-1").should("be.visible");
      cy.contains("[data-cy='tree-file']", "test-file-3").should("be.visible");
    });

    it("shows nested subfolders", () => {
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-3").click();
      cy.contains("[data-cy='tree-folder']", "test-sub-folder-1").should(
        "be.visible"
      );
    });

    it("expands nested subfolders to show deeply nested files", () => {
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-3").click();
      cy.contains("[data-cy='tree-folder']", "test-sub-folder-1").click();
      cy.contains("[data-cy='tree-file']", "test-file-5").should("be.visible");
    });
  });

  context("file loading", () => {
    it("loads a file when the load button is clicked", () => {
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");

      cy.contains("h1", "test-file-1").should("be.visible");
    });

    it("loads a root-level file", () => {
      cy.loadFile("test-file-2");

      cy.contains("h1", "test-file-2").should("be.visible");
    });

    it("shows no file display before a file is selected", () => {
      cy.contains("Select a CSV file to view its data").should("be.visible");
    });
  });

  context("tag filters", () => {
    it("displays tag filter options", () => {
      cy.expandTree();
      cy.get("[data-cy='tree-filter-header']").should("exist");
    });
  });
});
