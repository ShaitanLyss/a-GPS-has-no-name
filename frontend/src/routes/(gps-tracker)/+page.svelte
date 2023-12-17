<script lang="ts">
	import { MapLibre, Marker, type Map } from 'svelte-maplibre';
	import Fa from 'svelte-fa';
	import {faKiwiBird, type IconDefinition} from '@fortawesome/free-solid-svg-icons'
	import {faTwitter} from '@fortawesome/free-brands-svg-icons'
	import { onDestroy, onMount } from 'svelte';

	const icons: IconDefinition[] = [faKiwiBird, faTwitter]

	let map: Map | undefined;
	onMount(() => {
		console.log(map);
		
	});
</script>

<MapLibre
	style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
	class="relative w-full aspect-[9/16] max-h-[70vh] sm:max-h-full sm:aspect-video"
	standardControls
	bind:map={map}
>
	<Marker lngLat={[0, 0]}>
		<Fa icon={faKiwiBird}/>
	</Marker>
</MapLibre>
