<html>
	<head>
		<meta http-equiv="content-type" content="text/html; charset=UTF-8">
		<meta charset="utf-8">
		<title>RaspberryCast</title>
		<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
		<link href="{{get_url('static', filename='remote.css') }}" rel="stylesheet">
		<link href="{{get_url('static', filename='bootstrap.min.css') }}" rel="stylesheet">
		<link rel="icon" type="image/png" sizes="192x192" href="{{get_url('static', filename='favicon.png') }}" />
	</head>
	<body>
		<div id="content">
				<div id="message"></div>

				<form class="input-group">
					<input type="search" class="form-control input-lg" id="media-url" placeholder="Media's URL">
					<span id="clear-search" class="glyphicon glyphicon-remove-circle"></span>
				</form>

				<button id="cast-btn" class="btn btn-lg btn-success fifty" title="Cast now" type="button">
					<span class="tb">Cast</span>
					<span class="glyphicon glyphicon-send pull-right">
				</button>
				<button id="queue-btn" class="btn btn-lg btn-info fifty" title="Add current video to queue" type="button">
					<span class="tb">Queue</span>
					<span class="glyphicon glyphicon-menu-hamburger pull-right" >
				</button>

				<button id="pause-btn" class="fifty btn btn-info" type="button" title="Play/pause">
					<span class="glyphicon glyphicon-play"></span>
					<span class="glyphicon glyphicon-pause"></span>
				</button>
				<button id="stop-btn" class="fifty btn btn-danger" type="button" title="Stop video/Next queue video">
					<span class="glyphicon glyphicon-stop"></span>
				</button>

				<button id="backward-btn" class="fifty btn btn-warning" type="button" title="Backward">
					<span class="glyphicon glyphicon-backward pull-left"></span>
					<span class="tb">-30 seconds</span>
				</button>
				<button id="forward-btn" class="fifty btn btn-warning" type="button" title="Forward">
					<span class="tb">+30 seconds</span>
					<span class="glyphicon glyphicon-forward pull-right"></span>
				</button>

				<button id="vol-down-btn" class="fifty btn btn-primary" type="button" title="Lower volume">
					<span class="glyphicon glyphicon-volume-down"></span>
				</button>
				<button id="vol-up-btn" class="fifty btn btn-primary" type="button" title="Increase volume">
					<span class="glyphicon glyphicon-volume-up"></span>
				</button>

				<button id="next-video-btn" class="fifty btn btn-primary" type="button" title="Next video in playlist">
					<span class="tb">Next video</span>
					<span class="glyphicon glyphicon-step-forward pull-right"></span>
				</button>

				<button id="long-backward-btn" class="fifty btn btn-info" type="button" title="Long skip backwards">
					<span class="glyphicon glyphicon-backward pull-left"></span>
					<span class="tb">-10 minutes</span>
				</button>
				<button id="long-forward-btn" class="fifty btn btn-info" type="button" title="Long skip backwards">
					<span class="tb">+10 minutes</span>
					<span class="glyphicon glyphicon-forward pull-right"></span>
				</button>

				<!-- History and playlist management -->
				<button id="history-button-btn" class="ninety btn btn-warning" type="button" title="History" onClick="showHistory()">
					<span class="glyphicon glyphicon-list-alt  pull-left"></span>
					<span class="tb">History</span>
				</button>
				<div id="history-div" style="display:none">
				</div>
		</div>
		</center>


		<!-- script references -->

		<script src="{{get_url('static', filename='jquery-2.1.3.min.js') }}"></script>
		<script src="{{get_url('static', filename='history.js') }}"></script>
		<script src="{{get_url('static', filename='remote.js') }}"></script>
	</body>
</html>
