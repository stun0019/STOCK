async function loadSignals() {

    const response = await fetch(
        "http://localhost:8000/signals"
    );

    const signals = await response.json();

    const table =
        document.getElementById("signalTable");

    table.innerHTML = "";

    signals.data.forEach(signal => {

        table.innerHTML += `
        <tr>
            <td>${signal.symbol}</td>
            <td>${signal.direction}</td>
            <td>${signal.entry}</td>
            <td>${signal.stop_loss}</td>
            <td>${signal.target}</td>
            <td>${signal.score}</td>
        </tr>
        `;
    });
}

loadSignals();

setInterval(loadSignals, 30000);
