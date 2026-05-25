document.addEventListener("DOMContentLoaded", () => {
    // Determine the API base URL. If dashboard is running on port 18888, API is usually on 8000.
    const apiBaseUrl = `http://${window.location.hostname}:8000`;

    fetch(`${apiBaseUrl}/api/graph`)
        .then(res => res.json())
        .then(gData => {
            const Graph = ForceGraph3D()
              (document.getElementById('3d-graph'))
                .graphData(gData)
                .nodeLabel('id')
                .nodeAutoColorBy('group')
                .onNodeClick(node => {
                    // Trigger Documenter Agent to explain node
                    console.log("Clicked:", node.id);
                });
        })
        .catch(err => {
            console.error("Error fetching Neo4j graph data:", err);
            document.getElementById('info').innerText = "Error loading map data from API.";
        });
});
