document.addEventListener("DOMContentLoaded", () => {
    // Placeholder data - in a real app, this would fetch from a Neo4j proxy endpoint on FastAPI
    const gData = {
      nodes: [
          { id: "main.py", group: 1, val: 5 },
          { id: "orchestrator.py", group: 2, val: 3 },
          { id: "memory.py", group: 3, val: 2 }
      ],
      links: [
          { source: "main.py", target: "orchestrator.py" },
          { source: "orchestrator.py", target: "memory.py" }
      ]
    };

    const Graph = ForceGraph3D()
      (document.getElementById('3d-graph'))
        .graphData(gData)
        .nodeLabel('id')
        .nodeAutoColorBy('group')
        .onNodeClick(node => {
            // Trigger Documenter Agent to explain node
            console.log("Clicked:", node.id);
        });
});
