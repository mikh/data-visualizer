describe("File Display", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  context("file metadata for CSV file with stats", () => {
    beforeEach(() => {
      // Load test-file-1 (CSV with tags and file_stats)
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");
    });

    it("displays the file name", () => {
      cy.contains("h1", "test-file-1").should("be.visible");
    });

    it("displays the file path", () => {
      cy.contains("test-folder-1/test-file-1").should("be.visible");
    });

    it("displays the file type", () => {
      cy.contains("csv file").should("be.visible");
    });
  });

  context("tags", () => {
    it("displays tags for a file that has them", () => {
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");

      cy.contains("span", "tag-1").should("be.visible");
      cy.contains("span", "tag-2").should("be.visible");
    });

    it("displays tags with colored backgrounds", () => {
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");

      cy.contains("span.rounded-full", "tag-1")
        .invoke("css", "background-color")
        .should("not.eq", "rgba(0, 0, 0, 0)");
    });

    it("does not display tags section for a file with no tags", () => {
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-3").click();
      cy.contains("[data-cy='tree-folder']", "test-sub-folder-1").click();
      cy.loadFile("test-file-5");

      // File should load but no tag badges should appear
      cy.contains("h1", "test-file-5").should("be.visible");
      cy.get(".rounded-full").should("not.exist");
    });
  });

  context("file statistics", () => {
    beforeEach(() => {
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");
    });

    it("displays the file statistics section", () => {
      cy.contains("button", "File Statistics").should("be.visible");
    });

    it("shows file stats expanded by default", () => {
      cy.contains("Num Columns").should("be.visible");
      cy.contains("Num Rows").should("be.visible");
    });

    it("displays correct stat values", () => {
      // baseline-db.json has num_columns: 2, num_rows: 2 for test-file-1
      cy.contains("td", "Num Columns")
        .siblings("td")
        .should("contain", "2");
      cy.contains("td", "Num Rows")
        .siblings("td")
        .should("contain", "2");
    });

    it("collapses file statistics when header is clicked", () => {
      cy.contains("button", "File Statistics").click();
      cy.contains("td", "Num Columns").should("not.exist");
    });

    it("re-expands file statistics when header is clicked again", () => {
      cy.contains("button", "File Statistics").click();
      cy.contains("button", "File Statistics").click();
      cy.contains("td", "Num Columns").should("be.visible");
    });
  });

  context("column statistics", () => {
    beforeEach(() => {
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");
    });

    it("displays the column statistics section", () => {
      cy.contains("button", "Column Statistics").should("be.visible");
    });

    it("shows column names in the stats table", () => {
      // Column Statistics starts expanded, so no need to click
      // test-file-1 has columns: column-1, column-5
      cy.contains("button", "Column Statistics").scrollIntoView();
      cy.contains("td", "column-1").scrollIntoView().should("be.visible");
      cy.contains("td", "column-5").scrollIntoView().should("be.visible");
    });

    it("shows data type for each column", () => {
      // Column Statistics starts expanded, so no need to click
      cy.contains("button", "Column Statistics").scrollIntoView();
      cy.contains("td", "string").scrollIntoView().should("be.visible");
    });
  });

  context("file without stats", () => {
    it("does not show file statistics for a JSON file without stats", () => {
      cy.loadFile("test-file-2");

      cy.contains("h1", "test-file-2").should("be.visible");
      cy.contains("json file").should("be.visible");
      cy.contains("button", "File Statistics").should("not.exist");
    });
  });

  context("switching between files", () => {
    it("updates the display when a different file is loaded", () => {
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");
      cy.contains("h1", "test-file-1").should("be.visible");
      cy.contains("csv file").should("be.visible");

      // Load a different file
      cy.loadFile("test-file-2");
      cy.contains("h1", "test-file-2").should("be.visible");
      cy.contains("json file").should("be.visible");
    });
  });
});
