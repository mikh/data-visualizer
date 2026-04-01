module.exports = {
  presets: [
    ["@babel/preset-env", { targets: { node: "current" } }],
    ["@babel/preset-react", { runtime: "automatic" }],
  ],
  plugins: [
    // Transform import.meta.env → process.env for Jest compatibility
    function () {
      return {
        visitor: {
          MetaProperty(path) {
            // Replace import.meta.env.X with process.env.X
            path.replaceWithSourceString("{ env: process.env }");
          },
        },
      };
    },
  ],
};
