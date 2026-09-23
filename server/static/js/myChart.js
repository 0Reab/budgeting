function renderChart(data, labels) {
    var ctx = document.getElementById("myChart").getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'This year',
                data: data[0],
            },{
                label: 'Last year',
                data: data[1],
            }]
        },
        options: {scales:{yAxes:[{ticks:{beginAtZero:true}}]}}
    });
}

$("#renderBtn").click(
    function () {
        data = [110000,100000,80000,160000,160000,140000,130000,190000,180000,160000,110000,130200];
        data_2 = [100000,140000,90000,130000,180000,150000,130000,170000,140000,150000,100000,140200];
        data_all = [data, data_2]

        labels =  ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

        renderChart(data_all, labels);
    }
);
