import Header from "./Header.jsx";

export default function App() {
  return (
    <div>
      <Header />
      <div className="p-8 bg-red-500 text-white">
        <h1 className="text-4xl font-bold">Hello World</h1>
        <p className="text-lg">
          This should be red background with white text if Tailwind is working!
        </p>
      </div>
    </div>
  );
}
