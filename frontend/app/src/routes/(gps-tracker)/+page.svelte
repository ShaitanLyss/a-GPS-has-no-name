<script lang="ts">
	import { MapLibre, Marker, type LngLatLike } from 'svelte-maplibre';
	import Fa from 'svelte-fa';
	import { faKiwiBird, type IconDefinition } from '@fortawesome/free-solid-svg-icons';
	import { faTwitter } from '@fortawesome/free-brands-svg-icons';
	import { graphql } from '$houdini';

	const icons: IconDefinition[] = [faKiwiBird, faTwitter];

	let trackedObjects: Map<string, { ip: string; location: LngLatLike }> = new Map();

	// Handle updates
	const updates = graphql(`
		subscription TrackedObjectsUpdated {
			objectsUpdated {
				ip
				location {
					lat
					lng
				}
			}
		}
	`);

	$: updates.listen();
	$: if ($updates.data) {
		for (const obj of $updates.data.objectsUpdated) {
			trackedObjects.set(obj.ip, obj);
			trackedObjects = trackedObjects;
		}
	}
</script>

<MapLibre
	style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
	class="relative w-full aspect-[9/16] max-h-[70vh] sm:max-h-full sm:aspect-video"
	standardControls
>
	{#each trackedObjects as [_, trackedObject], i (trackedObject.ip)}
		<Marker lngLat={trackedObject.location}>
			<div title={trackedObject.ip}>
				<Fa icon={icons[i % icons.length]} />
			</div>
		</Marker>
	{/each}
</MapLibre>
