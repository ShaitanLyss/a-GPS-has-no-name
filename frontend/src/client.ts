import { HoudiniClient, subscription } from '$houdini';
import { createClient } from 'graphql-ws';

export default new HoudiniClient({
    url: 'http://localhost:8000/graphql',
    plugins: [
        subscription(() => createClient({
            url: 'ws://localhost:8000/graphql'
        }))
    ]

    // uncomment this to configure the network call (for things like authentication)
    // for more information, please visit here: https://www.houdinigraphql.com/guides/authentication
    // fetchParams({ session }) {
    //     return {
    //         headers: {
    //             Authentication: `Bearer ${session.token}`,
    //         }
    //     }
    // }
})
