const URL_PREFIX = import.meta.env.VITE_URL_PREFIX || "http://127.0.0.1:5000";

/**
 * Loads the tree and tags from the server.
 *
 * @param {Function} setStructure - The function to set the structure.
 * @param {Function} setTags - The function to set the tags.
 */
function loadTree(setStructure, setTags) {
  fetch(`${URL_PREFIX}/api/tree`, {
    method: "POST",
    body: JSON.stringify({
      control: "list",
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      setStructure(data.tree);
      setTags(data.tags);
    })
    .catch((error) => console.error("Error loading tree:", error));
}
