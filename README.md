<h1>LangGraphTask — Brief README</h1>

<p><strong>Model used:</strong> GigaChat Lite</p>
<p><strong>Recommended language:</strong> Russian (Others allowable)</p>
<p><strong>Features:</strong> An additional search tool based on the Tavily search engine was added to retrieve up-to-date information (for example, a horoscope 🙂).</p>
<h2>Installation</h2>
<ol>
  <li>Create a <code>.env</code> file with the variables <code>TAVILY_API_KEY</code> and <code>GIGACHAT_API</code></li>
  <li>Clone the repository and prepare the environment:
    <pre>git clone https://github.com/SoberSinceToday/LangGraphTask
cd LangGraphTask
python -m venv venv
.\venv\Scripts\Activate.ps1</pre>
  </li>
  <li>Install dependencies:
    <pre>pip install -r .\requirements.txt</pre>
  </li>
  <li>Run LangGraph:
    <pre>langgraph dev</pre>
  </li>
</ol>
