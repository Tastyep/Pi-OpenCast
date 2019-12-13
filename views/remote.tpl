<html>
	<head>
		<meta http-equiv="content-type" content="text/html; charset=UTF-8">
		<meta charset="utf-8">

		<title>OpenCast</title>
		<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">

		<link type="text/css" href="/static/opencast/css/remote.css" rel="stylesheet">
		<link type="text/css" href="/static/bootstrap/css/bootstrap.min.css" rel="stylesheet">
		<link type="text/css" href="/static/bootstrap4-toggle/css/bootstrap4-toggle.css" rel="stylesheet">
		<link type="image/png" href="/static/img/opencast.png" rel="icon" sizes="192x192"/>
	</head>
	<body>
		<div id="content">
				<div id="message"></div>

				<input type="checkbox" checked data-toggle="toggle" data-on="<i class='fa fa-play' aria-hidden='true'></i> Video">

				<form class="input-group">
					<input type="search" class="form-control input-lg" id="media-url" placeholder="Media's URL">
					<span id="clear-search" class="glyphicon glyphicon-remove-circle"></span>
				</form>

				<div id='button-line'>
					<button id="cast-btn" class="button-left btn btn-lg btn-success" title="Cast now" type="button">
						<span class="tb">Cast</span>
						<span class="glyphicon glyphicon-send pull-right">
					</button>
					<button id="queue-btn" class="button-right btn btn-lg btn-info" title="Add current video to queue" type="button">
						<span class="tb">Queue</span>
						<span class="glyphicon glyphicon-menu-hamburger pull-right" >
					</button>
				</div>

				<div class='button-line'>
					<button id="pause-btn" class="button-left btn btn-info" type="button" title="Play/pause">
						<span class="glyphicon glyphicon-play"></span>
						<span class="glyphicon glyphicon-pause"></span>
					</button>
					<button id="stop-btn" class="button-right btn btn-danger" type="button" title="Stop video/Next queue video">
						<span class="glyphicon glyphicon-stop"></span>
					</button>
				</div>

				<div class='button-line'>
					<button id="vol-down-btn" class="button-left btn btn-primary" type="button" title="Lower volume">
						<span class="glyphicon glyphicon-volume-down"></span>
					</button>
					<button id="vol-up-btn" class="button-right btn btn-primary" type="button" title="Increase volume">
						<span class="glyphicon glyphicon-volume-up"></span>
					</button>
				</div>

				<div class='button-line'>
					<button id="backward-btn" class="button-left btn btn-warning" type="button" title="Backward">
						<span class="glyphicon glyphicon-backward pull-left"></span>
						<span class="tb">-30 seconds</span>
					</button>
					<button id="forward-btn" class="button-right btn btn-warning" type="button" title="Forward">
						<span class="tb">+30 seconds</span>
						<span class="glyphicon glyphicon-forward pull-right"></span>
					</button>
				</div>

				<div class='button-line'>
					<button id="long-backward-btn" class="button-left btn btn-info" type="button" title="Long skip backwards">
						<span class="glyphicon glyphicon-backward pull-left"></span>
						<span class="tb">-5 minutes</span>
					</button>
					<button id="long-forward-btn" class="button-right btn btn-info" type="button" title="Long skip backwards">
						<span class="tb">+5 minutes</span>
						<span class="glyphicon glyphicon-forward pull-right"></span>
					</button>
				</div>

				<div class='button-line'>
					<button id="prev-video-btn" class="button-left btn btn-primary" type="button" title="Previous video">
						<span class="glyphicon glyphicon-step-backward pull-left"></span>
						<span class="tb">Previous video</span>
					</button>
					<button id="next-video-btn" class="button-right btn btn-primary" type="button" title="Next video">
						<span class="tb">Next video</span>
						<span class="glyphicon glyphicon-step-forward pull-right"></span>
					</button>
				</div>

				<div class='button-line'>
					<button id="toggle-subtitle-btn" class="btn btn-warning button-large" type="button" title="Toggle subtitle">
						<span class="glyphicon glyphicon-subtitles pull-left"></span>
						<span class="tb">Toggle subtitle</span>
					</button>
				</div>

				<div class='button-line'>
					<button id="dec-subtitle-delay" class="button-left btn btn-primary" type="button" title="Decrease delay">
						<span class="glyphicon glyphicon-backward pull-left"></span>
						<span class="tb">Decrease delay</span>
					</button>
					<button id="inc-subtitle-delay" class="button-right btn btn-primary" type="button" title="Increase delay">
						<span class="tb">Increase delay</span>
						<span class="glyphicon glyphicon-forward pull-right"></span>
					</button>
				</div>

				<!-- History and playlist management -->
				<div class='button-line'>
					<button id="history-btn" class="btn btn-warning button-large" type="button" title="History" onClick="showHistory()">
						<span class="glyphicon glyphicon-list-alt pull-left"></span>
						<span class="tb">History</span>
					</button>
				</div>
				<div id="history-div" style="display:none">
				</div>
		</div>
		</center>

		<!-- script references -->

		<script src="/static/jquery/js/jquery-3.4.1.min.js"></script>
		<script src="/static/bootstrap4-toggle/js/bootstrap4-toggle.js"></script>
		<script src="/static/opencast/js/history.js"></script>
		<script src="/static/opencast/js/remote.js"></script>
	</body>
</html>
