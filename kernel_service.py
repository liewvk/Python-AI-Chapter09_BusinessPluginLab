# kernel_service.py

from decimal import Decimal

from openai import AsyncOpenAI

from semantic_kernel import Kernel

from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion
)

from semantic_kernel.contents import ChatHistory

from semantic_kernel.functions import KernelArguments

from business_plugins import (
    CalculatorPlugin,
    ProductCatalogPlugin,
    BusinessOperationsPlugin,
    parse_amount
)

from settings import (
    OLLAMA_BASE_URL,
    MODEL_NAME,
    SERVICE_ID,
    TIMEOUT_SECONDS,
    TEMPERATURE,
    MAX_OUTPUT_TOKENS,
    SYSTEM_PROMPT
)


class BusinessKernelService:

    def __init__(self):

        # Create the Kernel.
        self.kernel = Kernel()

        # Create the native plugin objects.
        self.calculator = CalculatorPlugin()

        self.catalog = ProductCatalogPlugin()

        self.business = BusinessOperationsPlugin()

        # Register all three plugins.
        self.kernel.add_plugin(
            self.calculator,
            plugin_name="Calculator"
        )

        self.kernel.add_plugin(
            self.catalog,
            plugin_name="Catalog"
        )

        self.kernel.add_plugin(
            self.business,
            plugin_name="Business"
        )

        # Configure the local AI connection.
        self.api_client = AsyncOpenAI(
            base_url=OLLAMA_BASE_URL,
            api_key="ollama",
            timeout=TIMEOUT_SECONDS,
            max_retries=0
        )

        self.chat_service = OpenAIChatCompletion(
            ai_model_id=MODEL_NAME,
            service_id=SERVICE_ID,
            async_client=self.api_client
        )

        self.kernel.add_service(
            self.chat_service
        )

        self.settings = (
            self.kernel
            .get_prompt_execution_settings_from_service_id(
                SERVICE_ID
            )
        )

        self.settings.temperature = TEMPERATURE

        self.settings.max_tokens = MAX_OUTPUT_TOKENS

        # Request direct responses from supported
        # Ollama thinking models.
        self.settings.extra_body = {
            "reasoning_effort": "none"
        }

        self.last_result = None

    def list_registered_functions(self):
        """List all registered plugin functions."""

        output = []

        for plugin_name in (
            "Calculator",
            "Catalog",
            "Business"
        ):
            plugin = self.kernel.plugins[plugin_name]

            output.append(f"\n{plugin_name} Plugin:")

            for function_name in plugin.functions.keys():
                output.append(f"  - {function_name}")

        return "\n".join(output)
    async def invoke(
        self,
        plugin_name,
        function_name,
        **values
    ):
        """Invoke a selected Semantic Kernel function."""

        result = await self.kernel.invoke(
            plugin_name=plugin_name,
            function_name=function_name,
            arguments=KernelArguments(
                **values
            )
        )

        if result is None or result.value is None:

            raise ValueError(
                "The plugin returned no result."
            )

        if isinstance(result.value, Exception):

            raise ValueError(
                "The plugin operation failed."
            )

        text = str(result.value)

        self.last_result = text

        return text

    async def create_quotation(
        self,
        product_name,
        quantity,
        discount_percent
    ):
        """Combine product, calculator, and business plugins."""

        product = self.catalog.get_record(
            product_name
        )

        if product is None:

            raise ValueError(
                "The requested product does not exist."
            )

        if quantity < 1 or quantity > 1000:

            raise ValueError(
                "Quantity must be between 1 and 1000."
            )

        if quantity > product["stock"]:

            raise ValueError(
                "Requested quantity exceeds sample stock."
            )

        percent = parse_amount(
            discount_percent,
            "Discount percentage"
        )

        if percent > 100:

            raise ValueError(
                "Discount cannot exceed 100%."
            )

        # Retrieve product details through Semantic Kernel.
        details = await self.invoke(
            "Catalog",
            "get_product",
            product_name=product_name
        )

        # Calculate the purchase amount.
        calculation = await self.invoke(
            "Calculator",
            "calculate_total",
            unit_price=product["price"],
            quantity=quantity
        )

        # Calculate the discount.
        subtotal = (
            Decimal(product["price"]) * quantity
        )

        discounted = await self.invoke(
            "Business",
            "apply_discount",
            subtotal=str(subtotal),
            discount_percent=str(percent)
        )

        quotation = (
            "SAMPLE PRODUCT QUOTATION\n"
            "-------------------------\n"
            f"{details}\n\n"
            f"{calculation}\n\n"
            f"{discounted}\n\n"
            "Educational quotation only. "
            "No order has been placed."
        )

        self.last_result = quotation

        return quotation

    async def explain_last_result(self):
        """Ask Qwen 3.5 to explain the latest tool result."""

        if not self.last_result:

            raise ValueError(
                "Run a plugin operation first."
            )

        history = ChatHistory(
            system_message=SYSTEM_PROMPT
        )

        history.add_user_message(
            "Explain the following completed business "
            "operation to a beginner in no more than "
            "120 words.\n\n"
            "Do not recalculate amounts or invent facts.\n"
            "Use only the supplied result.\n\n"
            "BUSINESS RESULT:\n"
            f"{self.last_result}"
        )

        response = (
            await self.chat_service.get_chat_message_content(
                chat_history=history,
                settings=self.settings,
                kernel=self.kernel
            )
        )

        answer = (
            response.content
            if response is not None
            else None
        )

        if not answer or not answer.strip():

            raise ValueError(
                "Qwen 3.5 returned an empty explanation."
            )

        return answer.strip()

    async def close(self):
        """Close the HTTP client."""

        await self.api_client.close()

