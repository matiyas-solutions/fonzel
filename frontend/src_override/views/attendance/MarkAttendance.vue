<template>
	<BaseLayout>
		<template #header>
			<div class="flex items-center justify-between px-4 py-3 border-b bg-white">
				<div class="flex items-center gap-2">
					<Button variant="ghost" @click="router.back()">
						<FeatherIcon name="chevron-left" class="w-5 h-5" />
					</Button>
					<h1 class="text-xl font-bold text-gray-900">{{ __("Attendance") }}</h1>
				</div>
			</div>
		</template>
		<template #body>
			<div class="p-4 flex flex-col gap-6">
				<div class="bg-white rounded p-4 border flex flex-col gap-4">
					<FormControl
						label="Status"
						type="select"
						v-model="status"
						:options="[
							{ label: 'Present', value: 'Present' },
							{ label: 'Work From Home', value: 'Work From Home' },
							{ label: 'Half Day', value: 'Half Day' },
						]"
					/>

					<Button
						variant="solid"
						class="w-full py-4 text-base"
						:loading="attendanceResource.loading"
						@click="saveAttendance"
					>
						{{ __("Save") }}
					</Button>
				</div>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { ref, inject } from "vue"
import { useRouter } from "vue-router"
import { createResource, toast, FeatherIcon } from "frappe-ui"
import BaseLayout from "@/components/BaseLayout.vue"

const router = useRouter()
const __ = inject("$translate")

const status = ref("Present")

const attendanceResource = createResource({
	url: "fonzel.api.mark_attendance",
})

async function saveAttendance() {
	try {
		await attendanceResource.submit({ status: status.value })
		toast({
			title: __("Attendance Marked"),
			text: __("Your attendance has been recorded successfully."),
			variant: "success",
		})
		router.back()
	} catch (error) {
		console.error(error)
		toast({
			title: __("Error"),
			text: error.messages?.[0] || __("Failed to mark attendance"),
			variant: "error",
		})
	}
}
</script>
