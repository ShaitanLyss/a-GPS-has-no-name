import { browser, dev } from '$app/environment';
import { HoudiniClient, subscription } from '$houdini';
import { createClient } from 'graphql-ws';
// import { env as privateEnv} from '$env/dynamic/private';
import { env } from '$env/dynamic/public';

const public_addr = env.PUBLIC_BACKEND_ADDRESS + '/graphql';
let private_addr = '';
if (!browser) {
    private_addr =dev ? public_addr : public_addr.replace('localhost', 'backend');
}

export default new HoudiniClient({
    url: browser ? public_addr : private_addr,
    plugins: [
        subscription(() => createClient({
            url: public_addr.replace('http', 'ws'),
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
