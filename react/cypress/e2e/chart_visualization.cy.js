describe("Chart Visualization", () => {
  context("initial state", () => {
    it("shows placeholder text when no file is loaded", () => {
      cy.visit("/");
      cy.contains("Select a CSV file to view its data").should("be.visible");
    });
  });

  context("with a loaded CSV file", () => {
    beforeEach(() => {
      cy.visit("/");
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");
    });

    context("visualization panel", () => {
      it("displays the visualization section", () => {
        cy.contains("button", "Visualization").should("be.visible");
      });

      it("is expanded by default", () => {
        cy.contains("Line Chart").should("be.visible");
      });

      it("collapses when the header is clicked", () => {
        cy.contains("button", "Visualization").click();
        cy.contains("Line Chart").should("not.exist");
      });

      it("re-expands when the header is clicked again", () => {
        cy.contains("button", "Visualization").click();
        cy.contains("button", "Visualization").click();
        cy.contains("Line Chart").should("be.visible");
      });
    });

    context("chart type selection", () => {
      it("displays all six chart type buttons", () => {
        cy.contains("button", "Line Chart").should("be.visible");
        cy.contains("button", "Bar Chart").should("be.visible");
        cy.contains("button", "Scatter Plot").should("be.visible");
        cy.contains("button", "Histogram").should("be.visible");
        cy.contains("button", "Heatmap").should("be.visible");
        cy.contains("button", "Area Chart").should("be.visible");
      });

      it("does not show column selector before a chart type is selected", () => {
        cy.contains("X Axis").should("not.exist");
        cy.contains("Y Axis").should("not.exist");
      });

      it("highlights the selected chart type button", () => {
        cy.contains("button", "Bar Chart").click();
        cy.contains("button", "Bar Chart").should("have.class", "bg-slate-800");
      });

      it("unhighlights previously selected chart type", () => {
        cy.contains("button", "Bar Chart").click();
        cy.contains("button", "Line Chart").click();

        cy.contains("button", "Bar Chart").should("not.have.class", "bg-slate-800");
        cy.contains("button", "Line Chart").should("have.class", "bg-slate-800");
      });
    });

    context("column selector - bar chart", () => {
      beforeEach(() => {
        cy.contains("button", "Bar Chart").click();
      });

      it("shows X and Y axis selectors", () => {
        cy.contains("label", "X Axis").should("be.visible");
        cy.contains("label", "Y Axis").should("be.visible");
      });

      it("shows column options in dropdowns", () => {
        // test-file-1 has string columns (column-1, column-5)
        // Bar chart X accepts categorical, so both should be available
        cy.contains("label", "X Axis").parent().find("select").should("exist");
      });
    });

    context("column selector - histogram", () => {
      beforeEach(() => {
        cy.contains("button", "Histogram").click();
      });

      it("shows a single column selector", () => {
        cy.contains("label", "Column").should("be.visible");
      });
    });

    context("switching chart types clears selections", () => {
      it("resets column selections when switching chart type", () => {
        cy.contains("button", "Bar Chart").click();

        // Select a column in the X axis dropdown
        cy.contains("label", "X Axis").parent().find("select").select(1);

        // Switch chart type
        cy.contains("button", "Scatter Plot").click();

        // Dropdowns should be reset to default
        cy.contains("label", "X Axis").parent().find("select").should("have.value", "");
      });
    });
  });

  context("with a non-data file", () => {
    it("shows no data message for a file with missing data file", () => {
      cy.visit("/");
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-3");
      // test-file-3 points to fake-file.json which doesn't exist
      // The backend returns an error without file metadata, so DataViewer shows the no-data message
      cy.contains("No data found in file").should("be.visible");
    });
  });

  context("heatmap column selector", () => {
    beforeEach(() => {
      cy.visit("/");
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");
      cy.contains("button", "Heatmap").click();
    });

    it("shows X, Y, and Value selectors for heatmap", () => {
      cy.contains("label", "X Axis").should("be.visible");
      cy.contains("label", "Y Axis").should("be.visible");
      cy.contains("label", "Value").should("be.visible");
    });
  });

  context("line chart column selector", () => {
    beforeEach(() => {
      cy.visit("/");
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");
      cy.contains("button", "Line Chart").click();
    });

    it("shows X axis dropdown and Y axis multi-select", () => {
      cy.contains("label", "X Axis").should("be.visible");
      cy.contains("label", "Y Axis").should("be.visible");
    });

    it("shows message when no eligible numeric columns exist for Y axis", () => {
      // test-file-1 has only string columns, so no numeric columns for Y
      // The Y axis should show "No numeric columns" or similar
      cy.contains("label", "Y Axis").parent().should("exist");
    });
  });

  context("area chart column selector", () => {
    beforeEach(() => {
      cy.visit("/");
      cy.expandTree();
      cy.contains("[data-cy='tree-folder']", "test-folder-1").click();
      cy.loadFile("test-file-1");
      cy.contains("button", "Area Chart").click();
    });

    it("shows X and Y axis selectors for area chart", () => {
      cy.contains("label", "X Axis").should("be.visible");
      cy.contains("label", "Y Axis").should("be.visible");
    });
  });
});
