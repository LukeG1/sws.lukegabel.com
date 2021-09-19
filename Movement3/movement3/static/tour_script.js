$(function() {
  
    // define tour



    // id="dashboard-btn" class="list-group-item list-group-item-action bg-dark dark-bar" href="{{ url_for('dashboard') }}">Dashboard</a>
    //                 <a id="log-btn" class="list-group-item list-group-item-action bg-dark dark-bar" href="{{ url_for('log_exercises') }}">Log Exercises</a>
    //                 <a id="history-btn" class="list-group-item list-group-item-action bg-dark dark-bar" href="{{ url_for('history') }}">Your History</a>
    //                 <a id="exercises-btn" class="list-group-item list-group-item-action bg-dark dark-bar" href="{{ url_for('exercises') }}">Exercises</a>
    //                 <a id="stats-btn" class="list-group-item list-group-item-action bg-dark dark-bar" href="{{ url_for('stats') }}">Stats</a>
    //                 <a id="friends-btn" class="list-group-item list-group-item-action bg-dark dark-bar" href="{{ url_for('friends') }}">Friends</a>
    //                 <a id="start-btn" class="list-group-item list-group-item-action bg-dark dark-bar" href="{{ url_for('start_comp') }}">Start Comp</a>
    //                 <a id="join-btn" 
    var tour = new Tour({
        debug: true,
        basePath: location.pathname.slice(0, location.pathname.lastIndexOf('/')),
        steps: [
            {
                path: "/dashboard",
                element: "#dashboard-btn",
                title: "Dashboard",
                content: "Welcome to the dashboard, this is where you go to see the running comps you are in.",
                animation: false
            },
            {
                element: "#log-btn",
                title: "Log Exercises",
                content: "The log exercises is where you go to log.",
                animation: false
            },
            {
                path: "/logexercises",
                element: "#search_bar",
                title: "Search!",
                content: "this bar will be used to search for the exercises you want to log",
                animation: false,
                orphan: true,
            },
            {
                element: "#reps",
                title: "reps / weight",
                content: "this box is where you put the number of reps you did for an exercise, dome exercises have modifiers, for example weighted exercises.",
                animation: false,
                orphan: true,
            },
        ]
    });

    // init tour
    tour.init();

    // start tour
    $('#tutorial').click(function() {
        tour.restart();
        console.log("it started!")
    });

    
    

    });
