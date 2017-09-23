function graph(dates,prices,predicted_prices){
  console.log("HELLO")
  console.log("dates", dates);
  var ctx = document.getElementById("myChart");
  var myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [
        { 
          data: prices,
          label: "Actual Price",
          borderColor: "#3e95cd",
          backgroundColor: "#3e95cd",
          pointRadius: 0,
          fill: false
        },
        { 
          data: predicted_prices,
          label: "Predicted Price",
          borderColor: "#FF0000",
          backgroundColor: "#FF0000",
          pointRadius: 0,
          fill: false
        }

      ]
    },
    options: {
          scales: {
              xAxes: [{
                ticks: {
                    callback: function(tick,index,ticks){
                      if(tick%5 == 0)
                        return tick;
                      return null;
                    }

                }
            }]
          }
      },

  });
}

window.graph = graph