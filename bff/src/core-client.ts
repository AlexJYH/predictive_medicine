export type CoreBootstrap = {
  service: string;
  environment: string;
  capabilities: string[];
};

export async function getCoreBootstrap(
  coreApiUrl: string,
  requestId: string,
): Promise<CoreBootstrap> {
  const response = await fetch(`${coreApiUrl}/api/v1/app/bootstrap`, {
    headers: { "X-Request-ID": requestId },
    signal: AbortSignal.timeout(3_000),
  });
  if (!response.ok) {
    throw new Error(`core_unavailable:${response.status}`);
  }
  return (await response.json()) as CoreBootstrap;
}
