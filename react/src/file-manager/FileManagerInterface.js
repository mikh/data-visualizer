const URL_PREFIX = import.meta.env.VITE_URL_PREFIX || "http://127.0.0.1:5000";

/**
 * Loads the tree and tags from the server.
 *
 * @param {Function} setStructure - The function to set the structure.
 * @param {Function} setTags - The function to set the tags.
 */
export function loadTree(setStructure, setTags) {
  fetch(`${URL_PREFIX}/api/tree`, {
    method: "POST",
    body: JSON.stringify({
      control: "list",
    }),
    headers: {
      "Content-Type": "application/json; charset=utf-8",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      setStructure(data.tree);
      setTags(data.tags);
    })
    .catch((error) => console.error("Error loading tree:", error));
}

/**
 * Performs a request to the server.
 *
 * @param {Object} body : The body of the request.
 * @param {Function} setStructure : The function to set the structure.
 * @param {Function} setTags : The function to set the tags.
 */
function performRequest(body, setStructure, setTags) {
  fetch(`${URL_PREFIX}/api/tree`, {
    method: "POST",
    body: JSON.stringify(body),
    headers: {
      "Content-Type": "application/json; charset=utf-8",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error("Error:", data.error);
      }
      loadTree(setStructure, setTags);
    })
    .catch((error) => console.error("Error:", error));
}

/**
 * Deletes an object.
 *
 * @param {String} path : Path to delete the object at.
 * @param {Function} setStructure : The function to set the structure.
 * @param {Function} setTags : The function to set the tags.
 */
export function deleteObject(path, setStructure, setTags) {
  performRequest(
    {
      control: "delete",
      path: path,
    },
    setStructure,
    setTags
  );
}

/**
 * Moves an object.
 *
 * @param {String} src : Source path.
 * @param {String} dst : Destination path.
 * @param {Function} setStructure : The function to set the structure.
 * @param {Function} setTags : The function to set the tags.
 */
export function moveObject(src, dst, setStructure, setTags) {
  performRequest(
    {
      control: "move",
      source: src,
      dest: dst,
    },
    setStructure,
    setTags
  );
}

/**
 * Copies an object.
 *
 * @param {String} src : source path to copy from.
 * @param {String} dst : destination path to copy to.
 * @param {Function} setStructure : The function to set the structure.
 * @param {Function} setTags : The function to set the tags.
 */
export function copyObject(src, dst, setStructure, setTags) {
  performRequest(
    {
      control: "copy",
      source: src,
      dest: dst,
    },
    setStructure,
    setTags
  );
}

/**
 * Loads an object.
 *
 * @param {String} path : Path to load the object at.
 * @param {Function} loadFile : The function to load the file.
 */
export function loadObject(path, loadFile) {
  fetch(`${URL_PREFIX}/api/tree`, {
    method: "POST",
    body: JSON.stringify({
      control: "load",
      path: path,
    }),
    headers: {
      "Content-Type": "application/json; charset=utf-8",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error("Error:", data.error);
      }
      loadFile(data.data);
    })
    .catch((error) => console.error("Error:", error));
}

/**
 * Uploads a file.
 *
 * @param {File} file : The file to upload.
 * @param {String} path : The path to upload the file to.
 * @param {Function} setStructure : The function to set the structure.
 * @param {Function} setTags : The function to set the tags.
 */
export function uploadFile(file, path, setStructure, setTags) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("path", path);

  fetch(`${URL_PREFIX}/api/upload`, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error("Error:", data.error);
      }
      loadTree(setStructure, setTags);
    })
    .catch((error) => console.error("Error:", error));
}

/**
 * Updates an object.
 *
 * @param {String} path : Path to update the object at.
 * @param {Object} updateData : The data to update the object with.
 * @param {Function} setStructure : The function to set the structure.
 * @param {Function} setTags : The function to set the tags.
 */
export function updateObject(path, updateData, setStructure, setTags) {
  performRequest(
    {
      control: "update",
      path: path,
      ...updateData,
    },
    setStructure,
    setTags
  );
}
