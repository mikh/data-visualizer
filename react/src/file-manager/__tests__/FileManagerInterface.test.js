import {
  loadTree,
  deleteObject,
  moveObject,
  copyObject,
  loadObject,
  uploadFile,
  updateObject,
} from "../FileManagerInterface";

// ─── Setup ──────────────────────────────────────────────────────────────────

let fetchMock;
let consoleErrorSpy;

beforeEach(() => {
  fetchMock = jest.fn();
  global.fetch = fetchMock;
  consoleErrorSpy = jest.spyOn(console, "error").mockImplementation(() => {});
  delete window.confirm;
  window.confirm = jest.fn();
});

afterEach(() => {
  jest.restoreAllMocks();
});

function mockFetchResponse(data) {
  return fetchMock.mockResolvedValueOnce({
    json: () => Promise.resolve(data),
  });
}

function mockFetchError(error) {
  return fetchMock.mockRejectedValueOnce(error);
}

// ─── loadTree ───────────────────────────────────────────────────────────────

describe("loadTree", () => {
  it("fetches /api/tree with list control and sets structure and tags", async () => {
    const setStructure = jest.fn();
    const setTags = jest.fn();
    const treeData = { tree: [{ name: "file.csv" }], tags: ["tag1"] };
    mockFetchResponse(treeData);

    loadTree(setStructure, setTags);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledWith("/api/tree", {
      method: "POST",
      body: JSON.stringify({ control: "list" }),
      headers: { "Content-Type": "application/json; charset=utf-8" },
    });
    expect(setStructure).toHaveBeenCalledWith(treeData.tree);
    expect(setTags).toHaveBeenCalledWith(treeData.tags);
  });

  it("logs error on fetch failure", async () => {
    const error = new Error("network failure");
    mockFetchError(error);

    loadTree(jest.fn(), jest.fn());
    await flushPromises();

    expect(consoleErrorSpy).toHaveBeenCalledWith("Error loading tree:", error);
  });
});

// ─── deleteObject ───────────────────────────────────────────────────────────

describe("deleteObject", () => {
  it("sends delete request with correct path", async () => {
    const setStructure = jest.fn();
    const setTags = jest.fn();
    // First call: delete response, second call: loadTree response
    mockFetchResponse({});
    mockFetchResponse({ tree: [], tags: [] });

    deleteObject("/path/to/file", setStructure, setTags);
    await flushPromises();

    const firstCall = fetchMock.mock.calls[0];
    expect(firstCall[0]).toBe("/api/tree");
    expect(JSON.parse(firstCall[1].body)).toEqual({
      control: "delete",
      path: "/path/to/file",
    });
  });

  it("reloads tree after successful delete", async () => {
    mockFetchResponse({});
    mockFetchResponse({ tree: ["new_tree"], tags: ["new_tags"] });

    const setStructure = jest.fn();
    const setTags = jest.fn();
    deleteObject("/file", setStructure, setTags);
    await flushPromises();

    // Second fetch is the loadTree call
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(setStructure).toHaveBeenCalledWith(["new_tree"]);
  });

  it("prompts for force delete on file_not_found error", async () => {
    mockFetchResponse({ error_type: "file_not_found" });
    window.confirm.mockReturnValue(false);

    deleteObject("/missing", jest.fn(), jest.fn());
    await flushPromises();

    expect(window.confirm).toHaveBeenCalledWith(expect.stringContaining("/missing"));
  });

  it("sends force delete when user confirms", async () => {
    mockFetchResponse({ error_type: "file_not_found" });
    window.confirm.mockReturnValue(true);
    // performRequest call + loadTree call
    mockFetchResponse({});
    mockFetchResponse({ tree: [], tags: [] });

    deleteObject("/missing", jest.fn(), jest.fn());
    await flushPromises();

    const forceCall = fetchMock.mock.calls[1];
    expect(JSON.parse(forceCall[1].body)).toEqual({
      control: "delete",
      path: "/missing",
      force: true,
    });
  });

  it("does not force delete when user cancels", async () => {
    mockFetchResponse({ error_type: "file_not_found" });
    window.confirm.mockReturnValue(false);

    deleteObject("/missing", jest.fn(), jest.fn());
    await flushPromises();

    // Only the initial delete call, no follow-up
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("logs generic errors", async () => {
    mockFetchResponse({ error: "something went wrong" });
    mockFetchResponse({ tree: [], tags: [] });

    deleteObject("/file", jest.fn(), jest.fn());
    await flushPromises();

    expect(consoleErrorSpy).toHaveBeenCalledWith("Error:", "something went wrong");
  });
});

// ─── moveObject ─────────────────────────────────────────────────────────────

describe("moveObject", () => {
  it("sends move request with source and dest", async () => {
    mockFetchResponse({});
    mockFetchResponse({ tree: [], tags: [] });

    moveObject("/src", "/dst", jest.fn(), jest.fn());
    await flushPromises();

    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body).toEqual({ control: "move", source: "/src", dest: "/dst" });
  });

  it("reloads tree after move", async () => {
    mockFetchResponse({});
    mockFetchResponse({ tree: ["t"], tags: ["g"] });

    const setStructure = jest.fn();
    const setTags = jest.fn();
    moveObject("/src", "/dst", setStructure, setTags);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(setStructure).toHaveBeenCalledWith(["t"]);
    expect(setTags).toHaveBeenCalledWith(["g"]);
  });
});

// ─── copyObject ─────────────────────────────────────────────────────────────

describe("copyObject", () => {
  it("sends copy request with source and dest", async () => {
    mockFetchResponse({});
    mockFetchResponse({ tree: [], tags: [] });

    copyObject("/src", "/dst", jest.fn(), jest.fn());
    await flushPromises();

    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body).toEqual({ control: "copy", source: "/src", dest: "/dst" });
  });
});

// ─── loadObject ─────────────────────────────────────────────────────────────

describe("loadObject", () => {
  it("sends load request and calls loadFile with response", async () => {
    const fileData = { name: "test.csv", data: [[1, 2]] };
    mockFetchResponse(fileData);

    const loadFile = jest.fn();
    loadObject("/path/to/file", loadFile);
    await flushPromises();

    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body).toEqual({ control: "load", path: "/path/to/file" });
    expect(loadFile).toHaveBeenCalledWith(fileData);
  });

  it("still calls loadFile even when response has error", async () => {
    const errorData = { error: "not found" };
    mockFetchResponse(errorData);

    const loadFile = jest.fn();
    loadObject("/bad", loadFile);
    await flushPromises();

    expect(consoleErrorSpy).toHaveBeenCalledWith("Error:", "not found");
    expect(loadFile).toHaveBeenCalledWith(errorData);
  });

  it("logs error on fetch failure", async () => {
    const error = new Error("network");
    mockFetchError(error);

    loadObject("/file", jest.fn());
    await flushPromises();

    expect(consoleErrorSpy).toHaveBeenCalledWith("Error:", error);
  });
});

// ─── uploadFile ─────────────────────────────────────────────────────────────

describe("uploadFile", () => {
  it("sends FormData to /api/upload", async () => {
    mockFetchResponse({});
    mockFetchResponse({ tree: [], tags: [] });

    const file = new File(["content"], "test.csv", { type: "text/csv" });
    uploadFile(file, "/uploads", jest.fn(), jest.fn());
    await flushPromises();

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/upload");
    expect(options.method).toBe("POST");
    expect(options.body).toBeInstanceOf(FormData);
    expect(options.body.get("file")).toBe(file);
    expect(options.body.get("path")).toBe("/uploads");
  });

  it("reloads tree after upload", async () => {
    mockFetchResponse({});
    mockFetchResponse({ tree: ["t"], tags: ["g"] });

    const setStructure = jest.fn();
    const setTags = jest.fn();
    const file = new File(["data"], "f.csv");
    uploadFile(file, "/", setStructure, setTags);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(setStructure).toHaveBeenCalledWith(["t"]);
  });
});

// ─── updateObject ───────────────────────────────────────────────────────────

describe("updateObject", () => {
  it("sends update request with path and merged updateData", async () => {
    mockFetchResponse({});
    mockFetchResponse({ tree: [], tags: [] });

    updateObject("/file", { name: "new_name", tags: ["a"] }, jest.fn(), jest.fn());
    await flushPromises();

    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body).toEqual({
      control: "update",
      path: "/file",
      name: "new_name",
      tags: ["a"],
    });
  });

  it("reloads tree after update", async () => {
    mockFetchResponse({});
    mockFetchResponse({ tree: [], tags: [] });

    const setStructure = jest.fn();
    updateObject("/file", {}, setStructure, jest.fn());
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});

// ─── Helper ─────────────────────────────────────────────────────────────────

function flushPromises() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}
